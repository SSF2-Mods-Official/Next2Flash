// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.Fox_Knockback_113

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class Fox_Knockback_113 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function Fox_Knockback_113()
        {
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }


    }
}//package fox_fla

