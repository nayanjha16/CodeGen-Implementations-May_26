// DesignPatternsSolid | kind=solid | label=srp | domain=audio | tier=minimal
package org.example.patterns;

// SRP: separate persistence from formatting for audio
class AudioRecord {
    public final String id;
    public final int amount;
    public AudioRecord(String id, int amount) { this.id = id; this.amount = amount; }
}

class AudioRepository {
    public String save(AudioRecord r) { return "saved-audio:" + r.id; }
}

public class AudioFormatter {
    public String format(AudioRecord r) { return r.id + "=" + r.amount; }
}
