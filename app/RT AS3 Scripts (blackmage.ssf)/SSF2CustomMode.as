// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2CustomMode

package 
{
    public class SSF2CustomMode extends SSF2BaseAPIObject 
    {

        public function SSF2CustomMode(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2CustomMode");
        }

        final public function getInitialGameSettings():*
        {
            return (_api.getInitialGameSettings());
        }

        public function getModeSettings():Object
        {
            return (_api.getModeSettings());
        }

        public function getStageClass():Class
        {
            return (null);
        }

        public function getStageMC():Class
        {
            return (null);
        }

        public function handleMatchComplete():void
        {
        }

        public function getSummary():String
        {
            return (_api.getSummary());
        }

        final public function startMatch(_arg_1:*):void
        {
            _api.startMatch(_arg_1);
        }

        final public function saveModeData(_arg_1:Object):Boolean
        {
            return (_api.saveModeData(_arg_1));
        }

        final public function endMode(_arg_1:Object):void
        {
            _api.endMode(_arg_1);
        }


    }
}//package 

