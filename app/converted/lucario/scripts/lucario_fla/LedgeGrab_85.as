package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeGrab_85 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function LedgeGrab_85()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
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

        internal function frame21():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

