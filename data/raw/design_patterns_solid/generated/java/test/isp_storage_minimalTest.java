package org.example.patterns;
public class StorageIspTest {
    public static void main(String[] args) {
        StorageStore st = new StorageStore();
        st.write("x");
        if (!StorageIspClient.mirror(st).equals("storage:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
