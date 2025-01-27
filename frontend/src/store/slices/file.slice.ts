import { Api } from "@/lib/api";
import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";

interface File {
  id: number;
  file: string;
  uploaded_at: string;
  filename: string;
  owner?: string;
  size: number;
  type: string;
}

interface FileState {
  files: File[];
  isPending: boolean;
  error?: string;
  isSuccess?: boolean;
}

const initialState: FileState = {
  files: [],
  isPending: false,
  error: "",
};

export const fetchFiles = createAsyncThunk("file/fetchFiles", async () => {
  const response = await Api.get("files", {
    withCredentials: true,
  });
  return response.data.data;
});

const fileSlice = createSlice({
  name: "file",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchFiles.pending, (state) => {
        state.isPending = true;
      })
      .addCase(fetchFiles.fulfilled, (state, action: PayloadAction<File[]>) => {
        state.files = action.payload;
        state.isPending = false;
        state.isSuccess = true;
      })
      .addCase(fetchFiles.rejected, (state, action) => {
        state.error = action.error.message || "Failed to fetch files";
        state.isPending = false;
        state.isSuccess = false;
      });
  },
});

export default fileSlice.reducer;
