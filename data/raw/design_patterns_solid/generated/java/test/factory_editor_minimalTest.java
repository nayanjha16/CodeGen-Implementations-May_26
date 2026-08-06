package org.example.patterns;
public class EditorFactoryTest {
    public static void main(String[] args) {
        EditorFactory f = new EditorFactory();
        if (!f.create("basic").operate().equals("basic-editor")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-editor")) throw new AssertionError();
        System.out.println("ok");
    }
}
