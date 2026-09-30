package ai.training.service;

import java.util.Map;
import java.util.HashMap;

/** Result of a single training step. */
public final class TrainingStepResult {
    private final int batchIdx;
    private final float loss;
    private final Map<String, Float> facultyLosses;
    private final boolean success;
    private final String errorMsg;

    private TrainingStepResult(int batchIdx, float loss, Map<String, Float> facultyLosses,
                               boolean success, String errorMsg) {
        this.batchIdx = batchIdx;
        this.loss = loss;
        this.facultyLosses = facultyLosses;
        this.success = success;
        this.errorMsg = errorMsg;
    }

    public static TrainingStepResult success(int batchIdx, float loss, Map<String, Float> facultyLosses) {
        return new TrainingStepResult(batchIdx, loss, facultyLosses, true, "");
    }

    public static TrainingStepResult failure(String errorMsg) {
        return new TrainingStepResult(-1, Float.NaN, new HashMap<>(), false, errorMsg);
    }

    public int getBatchIdx()                  { return batchIdx; }
    public float getLoss()                    { return loss; }
    public Map<String, Float> getFacultyLosses() { return facultyLosses; }
    public boolean isSuccess()                { return success; }
    public String getErrorMsg()               { return errorMsg; }
}
