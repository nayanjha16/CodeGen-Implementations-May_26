package org.example.patterns;
public class NotesBuilderTest {
    public static void main(String[] args) {
        NotesConfig cfg = new NotesConfig.Builder().name("notes-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("notes-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
