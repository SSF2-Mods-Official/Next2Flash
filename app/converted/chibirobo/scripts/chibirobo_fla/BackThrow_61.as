package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class BackThrow_61 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:ChibiExt;

        public function BackThrow_61()
        {
            super();
            addFrameScript(0, this.frame1, 13, this.frame14, 21, this.frame22);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.swapDepthsWithGrabbedOpponent(true);
            };
        }

        internal function frame14():*
        {
            SSF2API.getCamera().shake(16);
            this.self.attachEffect("global_dust_cloud", {"x":this.self.flipX(-75)});
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }


    }
}

