// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Crouch_104

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_104 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Crouch_104()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
        }

        internal function frame4():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}//package blackmage_fla

