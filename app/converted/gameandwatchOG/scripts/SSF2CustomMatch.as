package
{
    public class SSF2CustomMatch extends SSF2BaseAPIObject
    {

        public var matchData:Object;

        public function SSF2CustomMatch(_arg_1:*):void
        {
            super(_arg_1);
            matchData = {};
        }

        override public function getType():String
        {
            return "SSF2CustomMatch";
        }

        public function getGameSettings():Object
        {
            return _api.getGameSettings();
        }

        public function matchSetup(_arg_1:Object):Object
        {
            return _arg_1;
        }


    }
}

