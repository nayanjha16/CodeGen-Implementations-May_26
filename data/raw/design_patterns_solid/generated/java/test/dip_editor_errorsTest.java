package org.example.patterns;
public class EditorDipTest {
    public static void main(String[] args) {
        String out = new EditorAppService(new EditorHttpGateway()).publish("p");
        if (!out.equals("http-editor:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
