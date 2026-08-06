package org.example.patterns;
public class SchedulingAdapterTest {
    public static void main(String[] args) {
        SchedulingTarget t = new SchedulingAdapter(new SchedulingLegacyApi());
        if (!t.fetch().equals("modern-scheduling")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
