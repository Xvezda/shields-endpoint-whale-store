# 웨일 스토어를 위한 shields.io 배지 엔드포인트 API 서버

![License](https://img.shields.io/github/license/Xvezda/shields-endpoint-whale-store)

[shields.io][1] 의 [엔드포인트 스키마](https://shields.io/endpoint)를 구현한 [웨일 스토어][2] 정보 제공 서드파티 API 서버 입니다.


## 기능

현재는 [웨일 스토어][2]에 업로드 된 확장앱의 버전정보만 지원하고 있습니다.


## 사용 예시

아래 URL은 시연을 위해 운영중인 API서버의 주소입니다.

`https://api.xvezda.com/v1/whale-store/v/{id}`

* URL구성
    * `v1`: [shields.io][1] 스키마 버전에 변동이 있을경우 하위호환등의 이유로 별도의 주소를 제공할 수 있도록 prefix로 사용되는 path 입니다. `main.py`의 `CustomFastAPI` 서브클래스로 `fastapi`를 상속하여 구현됩니다.
    * `v`: 대상의 버전 정보를 가져오는것을 나타냅니다.
    * `{id}`: 32자 영소문자로 구성된 웨일 스토어 ID값입니다. 각 상세페이지 URL의 끝자리를 통해 확인이 가능합니다. 예시로 다음의 확장앱 상세페이지 URL는 다음과 같은 ID값을 갖습니다.
        * URL: https://store.whale.naver.com/detail/ccamieeifalippbcdjfokaamepjpjcdo
        * ID: `ccamieeifalippbcdjfokaamepjpjcdo`


[shields.io][1]의 엔드포인트 URL은 다음과 같은 형식을 가집니다.

`https://img.shields.io/endpoint?url=...&style=...`


따라서 특정 확장앱의 버전 정보를 보여주는 [shields.io][1] 배지의 markdown은 다음과 같이 작성될 수 있습니다.

```markdown
[![FixImg](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.xvezda.com%2Fv1%2Fwhale-store%2Fv%2Fccamieeifalippbcdjfokaamepjpjcdo)](https://store.whale.naver.com/detail/ccamieeifalippbcdjfokaamepjpjcdo)
```

렌더링된 마크업의 결과는 아래와같이 보이게됩니다.

[![FixImg](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.xvezda.com%2Fv1%2Fwhale-store%2Fv%2Fccamieeifalippbcdjfokaamepjpjcdo)](https://store.whale.naver.com/detail/ccamieeifalippbcdjfokaamepjpjcdo)

[shields.io][1]에서는 다음 URL을 통해 엔드포인트 스키마에 관한 정보와 커스터마이징을 위한 웹 인터페이스를 제공하고 있습니다.

https://shields.io/endpoint


## 호스팅

개인서버에 호스팅하기 위해선 현 저장소를 `git`을 이용해 `clone`하여 설치하는것도 가능하지만, docker hub에 이미지를 배포중이므로 아래의 명령어를 통해 간편하고 빠르게 배포하는것이 가능합니다.

```sh
docker run xvezda/shields-endpoint-whale-store
```


[1]: https://shields.io/
[2]: https://store.whale.naver.com/
