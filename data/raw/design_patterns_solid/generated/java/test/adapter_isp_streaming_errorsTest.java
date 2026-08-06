package org.example.patterns;
public class StreamingAdapterTest {
    public static void main(String[] args) {
        StreamingTarget t = new StreamingAdapter(new StreamingLegacyApi());
        if (!t.fetch().equals("modern-streaming")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
