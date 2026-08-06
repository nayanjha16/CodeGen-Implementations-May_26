package org.example.patterns;
public class EditorAdapterTest {
    public static void main(String[] args) {
        EditorTarget t = new EditorAdapter(new EditorLegacyApi());
        if (!t.fetch().equals("modern-editor")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
