package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Hang_96 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Hang_96()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 50, this.frame51);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
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

        internal function frame51():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

