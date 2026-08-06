package org.example.patterns;
public class SchedulingIspTest {
    public static void main(String[] args) {
        SchedulingStore st = new SchedulingStore();
        st.write("x");
        if (!SchedulingIspClient.mirror(st).equals("scheduling:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
