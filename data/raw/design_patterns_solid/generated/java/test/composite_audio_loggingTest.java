package org.example.patterns;
public class AudioCompositeTest {
    public static void main(String[] args) {
        AudioComposite root = new AudioComposite();
        root.add(new AudioLeaf(2));
        root.add(new AudioLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
