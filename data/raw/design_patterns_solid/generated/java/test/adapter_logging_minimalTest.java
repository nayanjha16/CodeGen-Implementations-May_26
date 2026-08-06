package org.example.patterns;
public class LoggingAdapterTest {
    public static void main(String[] args) {
        LoggingTarget t = new LoggingAdapter(new LoggingLegacyApi());
        if (!t.fetch().equals("modern-logging")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
