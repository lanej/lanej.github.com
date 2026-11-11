use super::{
    policy::Publication,
    workflow::{ReviewPublisher, WriteOutcome},
};
use std::{num::NonZeroU64, sync::Mutex};

/// Offline substitute for either code-host adapter.
#[derive(Default)]
pub struct MemoryPublisher(Mutex<Vec<Publication>>);

impl MemoryPublisher {
    pub fn count(&self) -> usize {
        self.0.lock().unwrap().len()
    }
}

impl ReviewPublisher for MemoryPublisher {
    async fn publish(&self, publication: &Publication) -> WriteOutcome {
        let mut publications = self.0.lock().unwrap();
        publications.push(publication.clone());
        WriteOutcome::Published(NonZeroU64::new(publications.len() as u64).unwrap())
    }
}
