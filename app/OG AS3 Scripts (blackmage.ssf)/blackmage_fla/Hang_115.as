// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Hang_115

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Hang_115 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Hang_115()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 44, this.frame45);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setAttackEnabled(true, "b_forward");
                this.self.setAttackEnabled(true, "b_forward_air");
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("ledgeGrab_gfx", {
                "x":this.self.flipX(0),
                "y":0,
                "scaleX":-0.4,
                "scaleY":-0.4
            });
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}//package blackmage_fla

