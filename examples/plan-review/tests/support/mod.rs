use std::{
    io::{Read, Write},
    net::TcpListener,
    sync::{
        Arc,
        atomic::{AtomicBool, AtomicUsize, Ordering},
    },
    time::Duration,
};

pub struct Server {
    pub base: String,
    pub requests: Arc<AtomicUsize>,
    stop: Arc<AtomicBool>,
    thread: Option<std::thread::JoinHandle<()>>,
}

impl Server {
    pub fn new(
        handler: impl Fn(&str, &str, usize) -> Option<(u16, serde_json::Value, Option<String>)>
        + Send
        + 'static,
    ) -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        listener.set_nonblocking(true).unwrap();
        let base = format!("http://{}", listener.local_addr().unwrap());
        let requests = Arc::new(AtomicUsize::new(0));
        let stop = Arc::new(AtomicBool::new(false));
        let counter = requests.clone();
        let stopping = stop.clone();
        let thread = std::thread::spawn(move || {
            while !stopping.load(Ordering::SeqCst) {
                match listener.accept() {
                    Ok((mut stream, _)) => {
                        stream
                            .set_read_timeout(Some(Duration::from_secs(2)))
                            .unwrap();
                        let mut input = Vec::new();
                        let mut byte = [0u8; 1];
                        while !input.ends_with(b"\r\n\r\n") {
                            if stream.read(&mut byte).unwrap_or(0) == 0 {
                                break;
                            }
                            input.push(byte[0]);
                        }
                        let header = String::from_utf8(input).unwrap();
                        let length = header
                            .lines()
                            .find_map(|line| {
                                let (name, value) = line.split_once(':')?;
                                name.eq_ignore_ascii_case("content-length")
                                    .then(|| value.trim().parse::<usize>().unwrap())
                            })
                            .unwrap_or(0);
                        let mut body = vec![0; length];
                        stream.read_exact(&mut body).unwrap();
                        let count = counter.fetch_add(1, Ordering::SeqCst);
                        if let Some((status, value, link)) =
                            handler(&header, std::str::from_utf8(&body).unwrap(), count)
                        {
                            let body = value.to_string();
                            let link = link
                                .map(|value| format!("Link: {value}\r\n"))
                                .unwrap_or_default();
                            write!(stream, "HTTP/1.1 {status} Test\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n{link}\r\n{body}", body.len()).unwrap();
                        }
                    }
                    Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                        std::thread::sleep(Duration::from_millis(2))
                    }
                    Err(error) => panic!("fixture accept failed: {error}"),
                }
            }
        });
        Self {
            base,
            requests,
            stop,
            thread: Some(thread),
        }
    }
}
impl Drop for Server {
    fn drop(&mut self) {
        self.stop.store(true, Ordering::SeqCst);
        self.thread.take().unwrap().join().unwrap();
    }
}

pub async fn assert_publication(
    publisher: &impl plan_review::publish_review::workflow::ReviewPublisher,
) {
    use plan_review::{
        approve_plan::policy::Plan,
        memory::MemoryStore,
        publish_review::{
            policy::Review,
            workflow::{Outcome, WriteOutcome, publish_once},
        },
    };
    let plans = MemoryStore::new(Plan {
        id: "plan-a".into(),
        author: "sam".into(),
    });
    let review = Review {
        id: "review-7".into(),
        plan_id: "plan-a".into(),
        text: "Keep the backup.".into(),
    };
    assert!(matches!(
        publish_once(&review, &plans, publisher).await.unwrap(),
        Outcome::Attempted(WriteOutcome::Published(_))
    ));
}
