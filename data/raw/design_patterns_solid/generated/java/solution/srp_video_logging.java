// DesignPatternsSolid | kind=solid | label=srp | domain=video | tier=logging
package org.example.patterns;

// SRP: separate persistence from formatting for video
class VideoRecord {
    public final String id;
    public final int amount;
    public VideoRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class VideoRepository {
    public String save(VideoRecord r) { return "saved-video:" + r.id; }
}

public class VideoFormatter {
    public String format(VideoRecord r) { return r.id + "=" + r.amount; }
}
