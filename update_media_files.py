"""
app.py의 MEDIA_FILES를 media_files.json으로 복사
"""
import json

# app.py에서 가져온 완전한 MEDIA_FILES
MEDIA_FILES = {
    "기쁨": {"image": ["1fv7FADmEGxoWsa0nneM4H8SAHJ675Anp"], "video": ["1vo_HVDroVQpP8v6Z1c31lCHSB4qaL3nF"], "context": ["1wx8F1aN1SOWfaaawdSYB2KoNJgBD_BuW"]},
    "분노": {"image": ["1vfb5T2vOkR_WxMIMi-N3BQ5rwJlpEVUq"], "video": ["1cg0ntXkmqQeOT-DAuPDARqoLlqRCosxB"], "context": ["1iwFxh9buPcbqfv1djj2YUUEJISiK5vqj"]},
    "혐오": {"image": ["1jw5NO36f243Sp6wplc1R8JklLz06E3iC"], "video": ["1nRjJ9QZvRI9c578mErvotY9KfBw9W0Js"], "context": ["1wM2Sk6YvZ72ANBfBmAQ3ewh3tkMf2Rjg"]},
    "중립": {"image": ["12pm_q_pUJArqGw5l60k1YZrLSjBzMU4Y"], "video": ["1HJQvKSyFvMs3OluLARkUxWpt30PKf635"], "context": ["1xAzFkRlooY_6HusRd-X0zT97Gdz_agCE"]},
    "슬픔": {"image": ["1Z439Wc2-R09I5K7g0TGDa13qAGI-RCBp"], "video": ["12s0z9toDX3lfMRcdUwjQAyfgUvG_TlFo"], "context": ["1iOAH8hTOKcrwCOLyjf-z4HKBwM3uE3e1"]},
    "놀람": {"image": ["1EzGRc3b3ZrJ5KWtIavg8J7qoSHHRY75C"], "video": ["1025BftCg08x2809Ci37LcMYxzGOiFB2p"], "context": ["1TEKMRsWts-8SriOI0up4Hc6MIoF9IqO4"]},
    "공포": {"image": ["16ab_8uMPXYR_OWhwn-GW2z-FCyEdAUXb"], "video": ["1-AkeI0xWrST247vDNR9KO-km6fJ0y188"], "context": ["1rO60zjXGu5K0-Xm72dktsQGE7Uv2vRO4"]},
    "즐거움": {"image": ["1cMntV216JiXHrRyBJ4JKFaBnt3tSD5-z"], "video": ["16Uol3om5G2MLIcWPh25RRptsIxeWR3G5"], "context": ["1U2P9bnp7_sVYCqa86Z6_I-gm-4camQk-"]},
    "애원하는": {"image": ["1QEHraj991BQIqT5MJgzoaLeD0eyzf03p"], "video": ["1L8N6J_mIO0f4tAb7YoLY8LWp2s2qSam7"], "context": ["1JF6O1eZrbI8OEkWzJdfPsJqsoARyPHfO"]},
    "실망하는": {"image": ["10H67JnwDeUpHnLuIuSE56c7WjzKnh000"], "video": ["15oOTzsVi8b9PbSj_DKkLEDuJ09t-opy1"], "context": ["1hpmTQj2czi8DL7yRXF2ox0q4oNwGd0YF"]},
    "공감하는": {"image": ["1HzvOS1xzUfGHD8-rA7CHnTaQ_hgsXbQ7"], "video": ["1hP8LLCfhZSu2lWuA8sg1rKw6kpvbcSjq"], "context": ["17ZAgZv7jdPylW9SFi3kWWfSVBB4MEFAV"]},
    "충격받은": {"image": ["1KtAQgBFDt62LL4mdi7CaDNZ_pprwmVhx"], "video": ["1mkZB-sVrA1nwp2HmxCiFL2hGB3TE_pfR"], "context": ["1ZAaWg3TYJX7lYH2NBO3Z3pz1b801KRFf"]},
    "질투하는": {"image": ["1gE8BrJsQXvTa_SDhM6Eu94zc65wW0lmV"], "video": ["1l-5bTE_vjhCb0jGERr9qmm-7uQYBuLTq"], "context": ["1xPCmbzEPhM2OKAAVTS5b26iRUflu9Bgu"]},
    "초조한": {"image": ["1NLvpmf2IGIkGWu35MjcdBon4qOfWUxpY"], "video": ["1ZqAWW2rKsoU-eFizdxbM2t8CF3R3H7D3"], "context": ["1x8E8Tj3A-6oUpA2-68OJRqnyL-X9nRmI"]},
    "안심하는": {"image": ["1iPOFbVATnloUgSoEjkuYzFHcX36eBHSm"], "video": ["1w0yZHTAnhn1PVUx92lw5YxAo_dy3OoNH"], "context": ["1Yyj6mCKiGGevfk9mXlCRb1H_C8cbTF2u"]},
    "우울한": {"image": ["1TjfDqWOUtlKj67dL1vGPTKEUcQy0nchB"], "video": ["1iW5K_C4D_ercmX2_v8lVZNSoT4eKFb5t"], "context": ["1co7QJqn80bkp0fUnokdwQqYUPaPiS6IP"]},
    "불안한": {"image": ["1lxmA_sDqh0AULA_9ExbDgRS9I_2tFeP-"], "video": ["1NvrXor0niKLCjTfMwLYkmIp_jVYChuRZ"], "context": ["19wgT5CeK9AzKp5aNulf_xlyngiaoDohn"]},
    "사랑하는": {"image": ["1iT2-rFgOoerKsw9gi6zvYfQbdVESAw4h"], "video": ["1jI4h6X0ial8Lh93u4w6nloufAjk36mFA"], "context": ["1esvlLNRFCtKlB-lhNsEOfGphuSv0-hFF"]},
    "쌀쌀맞음": {"image": ["15m5MXNTNes69iQDlfkjqTfjmnIR3HFo8"], "video": ["1goPaSkqoC84fOgt08Fo64edMJgeWmU1g"], "context": ["1uAUculDrvbvMJwUYg31-LJVvWfhUPaJi"]},
    "활기찬": {"image": ["1iIJVmfhRV49TkfoQyyVaf_w-yoLi-_t5"], "video": ["1pbFnZV5ZVjK9hMaAtR11K91koEOKJpz_"], "context": ["14TSi83RKKEzb2cYbKIZxViwqTYsQs3Qb"]},
    "쑥스러운": {"image": ["1GMO7H-lHEepT2ELFrOtVzdMrsKpoG3o9"], "video": ["1lU_KfpUJjyviW6htZUjmJ3HzDJujqj5C"], "context": ["1vgekNQin5r2yi69FiSJubQ1bLAxFHvkj"]},
    "진지한": {"image": ["12dEIGSDhLCh438jiMfV-XI__HrDrotgC"], "video": ["1GWhCpYC1BKLH7znmZsFFH4KLtLcR2ZDx"], "context": ["1ZRv1MbRZjdQuO8me_4eCPz0NWGzAwX9k"]},
    "창피한": {"image": ["1wHbSk5eB2ZDQGJAs0fsGyS6y186zzu2b"], "video": ["1L04KawJrNgHiR96z13MuZSnRZkt5QjwF"], "context": ["1YVo1ztd4W9afbpC_YCOcorqrnBzO7Cqn"]},
}

# JSON으로 저장
with open("media_files.json", "w", encoding="utf-8") as f:
    json.dump(MEDIA_FILES, f, ensure_ascii=False, indent=2)

print("media_files.json 업데이트 완료!")
print(f"총 {len(MEDIA_FILES)}개 감정")

# 동영상 폴더 확인
video_count = sum(1 for emotion, data in MEDIA_FILES.items() if data.get("video"))
print(f"동영상 폴더가 있는 감정: {video_count}개")
