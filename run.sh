if [[ -z "${telegram_token}" ]]; then
  echo "No token was found for deployment. Exiting."
  exit 1
else
  docker build -t akkordknecht .
  docker run --env telegram_token=${telegram_token} akkordknecht
fi
