package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class star_290 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;

        public function star_290()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10, 11, this.frame12, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
        }

        internal function frame10():*
        {
            this.self.destroy();
        }

        internal function frame12():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame13():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("start");
            };
        }


    }
}

