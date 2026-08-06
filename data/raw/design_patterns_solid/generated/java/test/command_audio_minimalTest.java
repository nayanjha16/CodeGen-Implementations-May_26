package org.example.patterns;
public class AudioCommandTest {
    public static void main(String[] args) {
        AudioCommand cmd = new AudioActionCommand(new AudioReceiver(), "x");
        if (!cmd.execute().equals("done-audio:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
