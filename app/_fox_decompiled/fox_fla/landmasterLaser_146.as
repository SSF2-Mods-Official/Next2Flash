package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class landmasterLaser_146 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;
        public var FoxExt:*;

        public function landmasterLaser_146()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.FoxExt = this.self.getOwner();
            };
            if (SSF2API.isReady() && this.self)
            {
            };
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

