package org.example.patterns;
public class WidgetsDipTest {
    public static void main(String[] args) {
        String out = new WidgetsAppService(new WidgetsHttpGateway()).publish("p");
        if (!out.equals("http-widgets:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
