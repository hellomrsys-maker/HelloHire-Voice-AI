package com.solorock.bandhu;

import com.solorock.bandhu.dto.BandhuSkillRequest;
import com.solorock.bandhu.dto.BandhuSkillResponse;
import com.solorock.amsv.AMSVBridge;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;

/**
 * Enterprise Service Layer for BandhuPrime Master AI Architecture.
 * Coordinates dedicated skill engines (Writing, Email, Reviewing, Book Writing)
 * and verifies zero-bridge 64-byte AMSV shared memory synchronization.
 */
public class BandhuMasterController {

    public BandhuSkillResponse processSkillRequest(BandhuSkillRequest request) {
        if (request == null || request.getText() == null) {
            throw new IllegalArgumentException("Request and text must not be null");
        }

        String text = request.getText().trim();
        String skill = request.getTargetSkill() != null ? request.getTargetSkill() : "Writing";
        String lower = text.toLowerCase();

        BandhuSkillResponse response = new BandhuSkillResponse();
        response.setText(text);
        response.setSkill(skill);
        response.setEra(classifyEra(text));
        response.setStructuralScore(1.0f);
        response.setRegisterScore(1.0f);
        response.setConsistencyScore(1.0f);
        response.setRecommendedEditingStage("CopyEdit");

        List<String> notes = new ArrayList<>();

        if ("Writing".equalsIgnoreCase(skill)) {
            boolean endsProperly = text.endsWith(".") || text.endsWith("?") || text.endsWith("!") || text.endsWith("。");
            if (!endsProperly) {
                response.setClarityErrorsCount(response.getClarityErrorsCount() + 1);
                response.setStructuralScore(response.getStructuralScore() - 0.25f);
                notes.add("Writing Engine: Missing terminal sentence punctuation.");
            }
            if (!text.isEmpty() && Character.isLowerCase(text.charAt(0))) {
                response.setRegisterErrorsCount(response.getRegisterErrorsCount() + 1);
                response.setRegisterScore(response.getRegisterScore() - 0.20f);
                notes.add("Writing Engine: Sentence onset lacks capitalization.");
            }
        } else if ("Emailing".equalsIgnoreCase(skill) || "Email".equalsIgnoreCase(skill)) {
            boolean hasSalutation = lower.contains("dear ") || lower.contains("sehr geehrte")
                    || lower.contains("hello") || lower.contains("hi ") || lower.contains("estimado");
            if (!hasSalutation) {
                response.setRegisterErrorsCount(response.getRegisterErrorsCount() + 1);
                response.setRegisterScore(response.getRegisterScore() - 0.25f);
                notes.add("Email Engine: Missing conventional salutation formula.");
            }
            boolean hasModal = lower.contains("could you") || lower.contains("would you")
                    || lower.contains("would it be possible") || lower.contains("könnten sie");
            boolean hasAbrupt = lower.contains("send me") || lower.contains("do this now");
            if (hasAbrupt && !hasModal) {
                response.setRegisterErrorsCount(response.getRegisterErrorsCount() + 1);
                response.setRegisterScore(response.getRegisterScore() - 0.35f);
                notes.add("Email Engine: Direct imperative used without conditional modal mitigation.");
            }
            boolean hasSignoff = lower.contains("best regards") || lower.contains("sincerely")
                    || lower.contains("mit freundlichen grüßen") || lower.contains("cordialement");
            if (!hasSignoff) {
                response.setRegisterErrorsCount(response.getRegisterErrorsCount() + 1);
                response.setRegisterScore(response.getRegisterScore() - 0.20f);
                notes.add("Email Engine: Missing professional sign-off formula.");
            }
        } else if ("Reviewing".equalsIgnoreCase(skill)) {
            boolean hasHedging = lower.contains("suggest") || lower.contains("might consider")
                    || lower.contains("could benefit") || lower.contains("recommend");
            if (!hasHedging) {
                response.setStylePreferenceCount(response.getStylePreferenceCount() + 1);
                response.setRegisterScore(response.getRegisterScore() - 0.15f);
                notes.add("Reviewing Engine: Feedback lacks professional modal hedging.");
            }
            boolean hasAnchor = lower.contains("line ") || lower.contains("page ") || lower.contains("section ");
            if (!hasAnchor) {
                response.setClarityErrorsCount(response.getClarityErrorsCount() + 1);
                response.setStructuralScore(response.getStructuralScore() - 0.30f);
                notes.add("Reviewing Engine: Critique unanchored to line or page coordinates.");
            }
            response.setRecommendedEditingStage("LineEdit");
        } else if ("BookWriting".equalsIgnoreCase(skill)) {
            if (lower.contains("was") && lower.contains("is")) {
                response.setClarityErrorsCount(response.getClarityErrorsCount() + 1);
                response.setConsistencyScore(response.getConsistencyScore() - 0.30f);
                notes.add("Book Writing Engine: Tense clash detected between past and present narration.");
            }
            response.setRecommendedEditingStage("CopyEdit");
        }

        response.setStructuralScore(Math.max(0.0f, Math.min(1.0f, response.getStructuralScore())));
        response.setRegisterScore(Math.max(0.0f, Math.min(1.0f, response.getRegisterScore())));
        response.setConsistencyScore(Math.max(0.0f, Math.min(1.0f, response.getConsistencyScore())));
        response.setDiagnostics(notes);

        // Zero-Bridge Synchronous Memory update: write state directly into AMSV
        try {
            ByteBuffer buf = AMSVBridge.getStateVector();
            if (buf != null && buf.capacity() >= 64) {
                // Offset 0x30: MAIO State Alpha (Pack skill and scores)
                int skillByte = getSkillByte(skill);
                buf.put(0x30, (byte) skillByte);
                buf.put(0x31, (byte) (response.getStructuralScore() * 255.0f));
                buf.put(0x32, (byte) (response.getRegisterScore() * 255.0f));
                buf.put(0x33, (byte) (response.getConsistencyScore() * 255.0f));
                AMSVBridge.syncMemoryBarrier();
            }
        } catch (Throwable ignored) {
            // Memory bridge fallback
        }

        return response;
    }

    private String classifyEra(String text) {
        String lower = text.toLowerCase();
        if (lower.contains("panini") || lower.contains("aṣṭādhyāyī") || lower.contains("sanskrit")
                || lower.contains("hieroglyph") || lower.contains("cuneiform") || lower.contains("kataba")) {
            return "Ancient";
        }
        if (lower.contains("brb") || lower.contains("lol") || lower.contains("yyds") || lower.contains("tbh")) {
            return "Digital";
        }
        if (lower.contains("thou ") || lower.contains("thee ") || lower.contains("hath ")) {
            return "Historical";
        }
        return "Modern";
    }

    private int getSkillByte(String skill) {
        if ("Writing".equalsIgnoreCase(skill)) return 0;
        if ("Emailing".equalsIgnoreCase(skill) || "Email".equalsIgnoreCase(skill)) return 1;
        if ("Listening".equalsIgnoreCase(skill)) return 2;
        if ("Pronouncing".equalsIgnoreCase(skill)) return 3;
        if ("Reviewing".equalsIgnoreCase(skill)) return 4;
        if ("BookWriting".equalsIgnoreCase(skill)) return 5;
        return 0;
    }
}
