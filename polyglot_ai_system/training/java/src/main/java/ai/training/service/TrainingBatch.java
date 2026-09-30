package ai.training.service;

import java.util.List;
import java.util.Map;

/** A single training batch — token IDs and sequence lengths. */
public final class TrainingBatch {
    private final int   batchIndex;
    private final int[] tokenIds;
    private final int[] seqLengths;
    private final int   maxSeqLen;

    public TrainingBatch(int batchIndex, int[] tokenIds, int[] seqLengths, int maxSeqLen) {
        this.batchIndex = batchIndex;
        this.tokenIds   = tokenIds;
        this.seqLengths = seqLengths;
        this.maxSeqLen  = maxSeqLen;
    }

    public int   getBatchIndex()  { return batchIndex; }
    public int[] getTokenIds()    { return tokenIds; }
    public int[] getSeqLengths()  { return seqLengths; }
    public int   getMaxSeqLen()   { return maxSeqLen; }

    @SuppressWarnings("unchecked")
    public static TrainingBatch fromMap(Map<String, Object> m) {
        int batchIdx = ((Number) m.getOrDefault("batch_idx", 0)).intValue();
        List<Number> ids = (List<Number>) m.getOrDefault("token_ids", List.of());
        List<Number> lens = (List<Number>) m.getOrDefault("seq_lengths", List.of());
        int maxSeq = ((Number) m.getOrDefault("max_seq_len", 512)).intValue();

        int[] tokenIds = ids.stream().mapToInt(Number::intValue).toArray();
        int[] seqLengths = lens.stream().mapToInt(Number::intValue).toArray();
        return new TrainingBatch(batchIdx, tokenIds, seqLengths, maxSeq);
    }
}
