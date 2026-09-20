package com.example.packetivex.dto;

import lombok.*;
import java.util.List;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor
@Builder
public class AnalyticsDashboardResponse {
    private List<ProtocolDistribution> protocolDistribution;
    private List<AppTrafficSummary> topApps;
    private List<TimelinePoint> timelinePoints;
    private String highestConsumer;
}
