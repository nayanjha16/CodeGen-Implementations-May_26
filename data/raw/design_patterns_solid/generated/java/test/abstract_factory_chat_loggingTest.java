package org.example.patterns;
public class ChatAbstractFactoryTest {
    public static void main(String[] args) {
        String out = ChatAbstractFactoryDemo.run(new ChatCloudFactory());
        if (!out.equals("cloud-btn-chat|cloud-dlg-chat")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
