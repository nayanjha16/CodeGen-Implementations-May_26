#!/usr/bin/env bash
# Download OOP Java↔Python datasets for fine-tuning:
#   - AVATAR (whole programs + parallel functions)
#   - AVATAR-TC from CoTran (verified parallel pairs with test cases)
#   - ClassEval-T (class-level Java/Python benchmark)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="${SCRIPT_DIR}/../raw"

AVATAR_DIR="${RAW_DIR}/avatar"
AVATAR_TC_DIR="${RAW_DIR}/avatar_tc"
CLASSEVAL_DIR="${RAW_DIR}/classeval_t"

mkdir -p "${AVATAR_DIR}" "${AVATAR_TC_DIR}" "${CLASSEVAL_DIR}"

AVATAR_OK=0
AVATAR_TC_OK=0
CLASSEVAL_OK=0

is_valid_zip() {
    local archive="$1"
    [[ -f "${archive}" ]] && unzip -tq "${archive}" >/dev/null 2>&1
}

# Google Drive download (matches wasiahmad/AVATAR data/download.sh flow).
download_gdrive() {
    local file_id="$1"
    local dest_path="$2"

    if is_valid_zip "${dest_path}"; then
        echo "  Already present: ${dest_path}"
        return 0
    fi
    rm -f "${dest_path}"

    echo "  Downloading https://drive.google.com/file/d/${file_id} ..."
    local cookie_file page_file confirm
    cookie_file="$(mktemp)"
    page_file="$(mktemp)"

    if command -v wget >/dev/null 2>&1; then
        wget --save-cookies "${cookie_file}" -q \
            "https://docs.google.com/uc?export=download&id=${file_id}" \
            -O "${page_file}" || true
        confirm="$(sed -rn 's/.*confirm=([0-9A-Za-z_+-]+).*/\1/p' "${page_file}" | head -1)"
        if [[ -n "${confirm}" ]]; then
            wget --load-cookies "${cookie_file}" -q \
                "https://docs.google.com/uc?export=download&confirm=${confirm}&id=${file_id}" \
                -O "${dest_path}" || true
        else
            cp "${page_file}" "${dest_path}"
        fi
    else
        curl -c "${cookie_file}" -s -L \
            "https://docs.google.com/uc?export=download&id=${file_id}" \
            -o "${page_file}"
        confirm="$(sed -rn 's/.*confirm=([0-9A-Za-z_+-]+).*/\1/p' "${page_file}" | head -1)"
        if [[ -n "${confirm}" ]]; then
            curl -Lb "${cookie_file}" -s \
                "https://docs.google.com/uc?export=download&confirm=${confirm}&id=${file_id}" \
                -o "${dest_path}"
        else
            cp "${page_file}" "${dest_path}"
        fi
    fi

    rm -f "${cookie_file}" "${page_file}"

    if ! is_valid_zip "${dest_path}"; then
        rm -f "${dest_path}"
        return 1
    fi
}

sparse_clone() {
    local repo_url="$1"
    local dest_dir="$2"
    shift 2
    local -a paths=("$@")

    rm -rf "${dest_dir}"
    git clone --depth 1 --filter=blob:none --sparse "${repo_url}" "${dest_dir}"
    (
        cd "${dest_dir}"
        git sparse-checkout set "${paths[@]}"
    )
}

echo "==> Downloading OOP datasets into ${RAW_DIR}"

# --- AVATAR: data.zip + parallel_functions.zip (wasiahmad/AVATAR data/download.sh) ---
echo ""
echo "==> AVATAR (whole programs + parallel functions)"
if [[ -d "${AVATAR_DIR}/parallel_functions" ]] && [[ -n "$(ls -A "${AVATAR_DIR}/parallel_functions" 2>/dev/null)" ]]; then
    echo "AVATAR already present, skipping."
    AVATAR_OK=1
else
    # IDs from https://github.com/wasiahmad/AVATAR/blob/main/data/download.sh
    if download_gdrive "1ch8BCPmMfHFq8D7NRxmU0ps-Ymv80h4a" "${AVATAR_DIR}/data.zip" \
        && download_gdrive "1ql9nkGnfpOn27p8M_JtpgCpezbbjIOUD" "${AVATAR_DIR}/parallel_functions.zip"; then
        echo "  Extracting AVATAR archives..."
        unzip -q -o "${AVATAR_DIR}/data.zip" -d "${AVATAR_DIR}"
        unzip -q -o "${AVATAR_DIR}/parallel_functions.zip" -d "${AVATAR_DIR}"
        AVATAR_OK=1
        echo "AVATAR download complete."
    else
        echo "WARNING: AVATAR Google Drive archives are unavailable (upstream links may be broken)."
        echo "         See https://github.com/wasiahmad/AVATAR/tree/main/data — manual download may be required."
        echo "         Preprocessing can still proceed with AVATAR-TC + ClassEval-T."
    fi
fi

# --- AVATAR-TC from PrithwishJana/CoTran ---
echo ""
echo "==> AVATAR-TC (CoTran verified Java↔Python pairs)"
if [[ -f "${AVATAR_TC_DIR}/train.java-python.java" ]]; then
    echo "AVATAR-TC already present, skipping."
    AVATAR_TC_OK=1
else
    COTRAN_TMP="${RAW_DIR}/.cotran_sparse_clone"
    sparse_clone "https://github.com/PrithwishJana/CoTran.git" "${COTRAN_TMP}" "AVATAR-TC"
    cp -R "${COTRAN_TMP}/AVATAR-TC/." "${AVATAR_TC_DIR}/"
    rm -rf "${COTRAN_TMP}"
    AVATAR_TC_OK=1
    echo "AVATAR-TC download complete."
fi

# --- ClassEval-T: Java + Python class-level tasks ---
echo ""
echo "==> ClassEval-T (class-level Java/Python benchmark)"
if [[ -d "${CLASSEVAL_DIR}/ClassEval_T/java" ]]; then
    echo "ClassEval-T already present, skipping."
    CLASSEVAL_OK=1
else
    CLASSEVAL_TMP="${RAW_DIR}/.classeval_sparse_clone"
    sparse_clone "https://github.com/wLinHoo/ClassEval-T.git" "${CLASSEVAL_TMP}" \
        "ClassEval_T/java" "ClassEval_T/py"
    cp -R "${CLASSEVAL_TMP}/ClassEval_T" "${CLASSEVAL_DIR}/"
    rm -rf "${CLASSEVAL_TMP}"

    # Convenience symlinks matching plan layout (Java/ and Python/).
    ln -sfn "ClassEval_T/java" "${CLASSEVAL_DIR}/Java"
    ln -sfn "ClassEval_T/py" "${CLASSEVAL_DIR}/Python"
    CLASSEVAL_OK=1
    echo "ClassEval-T download complete."
fi

echo ""
echo "==> OOP dataset download finished."
echo "    AVATAR:       ${AVATAR_DIR} $([[ ${AVATAR_OK} -eq 1 ]] && echo '[ok]' || echo '[skipped — manual download needed]')"
echo "    AVATAR-TC:    ${AVATAR_TC_DIR} $([[ ${AVATAR_TC_OK} -eq 1 ]] && echo '[ok]' || echo '[failed]')"
echo "    ClassEval-T:  ${CLASSEVAL_DIR} $([[ ${CLASSEVAL_OK} -eq 1 ]] && echo '[ok]' || echo '[failed]')"
echo ""
echo "Next: python data/scripts/preprocess_java_oop.py --avatar-fraction 1.0 --design-upsample 2"

if [[ ${AVATAR_TC_OK} -eq 0 || ${CLASSEVAL_OK} -eq 0 ]]; then
    exit 1
fi
