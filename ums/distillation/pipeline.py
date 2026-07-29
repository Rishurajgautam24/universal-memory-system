import logging

from ums.memory.candidate import MemoryEngine
from ums.models.distillation import CycleStatus, DistillationCycle
from ums.storage.interface import Storage
from ums.utils.datetime import now_utc

logger = logging.getLogger(__name__)


class DistillationPipeline:
    def __init__(self, storage: Storage, memory_engine: MemoryEngine, batch_size: int = 10):
        self._storage = storage
        self._memory_engine = memory_engine
        self._batch_size = batch_size

    async def run(self) -> DistillationCycle:
        cycle = DistillationCycle(started_at=now_utc().isoformat(), status=CycleStatus.RUNNING)
        try:
            observations = await self._storage.dequeue_batch(self._batch_size)
            cycle.observations_read = len(observations)
            for obs in observations:
                try:
                    candidate = await self._memory_engine.process_observation(obs)
                    if candidate:
                        if candidate.status.value == "PROMOTED":
                            cycle.candidates_promoted += 1
                        elif candidate.status.value == "ACCUMULATING":
                            cycle.candidates_created += 1
                    await self._storage.mark_processed(obs.id)
                except Exception as e:
                    logger.error("obs_failed: %s", str(e))
                    cycle.errors.append(str(e))
            cycle.status = CycleStatus.COMPLETED
            cycle.completed_at = now_utc().isoformat()
            cycle.summary = f"Processed {cycle.observations_read} obs: {cycle.candidates_created} created, {cycle.candidates_promoted} promoted"
        except Exception as e:
            cycle.status = CycleStatus.FAILED
            cycle.errors.append(str(e))
        return cycle
