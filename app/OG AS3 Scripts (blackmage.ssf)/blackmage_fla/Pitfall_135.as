// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Pitfall_135

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Pitfall_135 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Pitfall_135()
        {
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setGlobalVariable("jab", false);
            };
        }


    }
}//package blackmage_fla

