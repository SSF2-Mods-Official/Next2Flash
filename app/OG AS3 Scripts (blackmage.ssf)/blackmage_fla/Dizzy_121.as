// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Dizzy_121

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_121 extends MovieClip 
    {

        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Dizzy_121()
        {
            addFrameScript(0, this.frame1, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.playSound("bm_Dizzy");
                this.self.setGlobalVariable("jab", false);
            };
        }

        internal function frame26():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}//package blackmage_fla

