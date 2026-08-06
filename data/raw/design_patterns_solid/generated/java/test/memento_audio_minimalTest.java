package org.example.patterns;
public class AudioMementoTest {
    public static void main(String[] args) {
        AudioOriginator o = new AudioOriginator();
        AudioMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("audio-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
