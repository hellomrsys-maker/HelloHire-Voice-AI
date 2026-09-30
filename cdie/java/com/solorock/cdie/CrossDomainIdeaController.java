package com.solorock.cdie;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.*;

/**
 * CrossDomainIdeaController — High-concurrency enterprise controller for CDIE.
 * Evaluates lateral thinking and interdisciplinary analogical transfer.
 */
public class CrossDomainIdeaController {

    private final ByteBuffer amsvBuffer;

    private static final List<String> CONNECTORS = Arrays.asList(
        "like a", "similar to how", "just as", "akin to", "analogous to", "draws inspiration from"
    );
    private static final List<String> BIO_TERMS = Arrays.asList(
        "dna", "cellular", "evolution", "immune", "antigen", "organism"
    );
    private static final List<String> TECH_TERMS = Arrays.asList(
        "latency", "cache", "throughput", "concurrency", "distributed", "database"
    );

    public CrossDomainIdeaController(ByteBuffer amsvBuffer) {
        if (amsvBuffer != null) {
            this.amsvBuffer = amsvBuffer.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            this.amsvBuffer = null;
        }
    }

    public Map<String, Object> evaluate(String text) {
        String lower = text.toLowerCase();

        boolean hasConnector = CONNECTORS.stream().anyMatch(lower::contains);
        boolean hasBio = BIO_TERMS.stream().anyMatch(lower::contains);
        boolean hasTech = TECH_TERMS.stream().anyMatch(lower::contains);

        boolean hasBridge = hasConnector && hasBio && hasTech;
        float distance = (hasBio && hasTech) ? 0.85f : 0.25f;
        float cdti = hasBridge ? 0.88f : ((hasBio && hasTech) ? 0.55f : (hasConnector ? 0.40f : 0.20f));
        int grade = cdti >= 0.75f ? 1 : (cdti >= 0.55f ? 2 : (cdti >= 0.35f ? 3 : 4));

        Map<String, Object> res = new HashMap<>();
        res.put("has_bridge", hasBridge);
        res.put("manifold_distance", distance);
        res.put("cross_domain_transfer_index", cdti);
        res.put("transfer_grade", grade);
        return res;
    }
}
