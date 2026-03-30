package
{
    import flash.display.MovieClip;

    public dynamic class a extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;

        public function a()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 15, this.frame16, 16, this.frame17, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
        }

        internal function frame2():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "direction":45,
                "power":60,
                "kbConstant":30
            });
        }

        internal function frame16():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame17():*
        {
            this.self = SSF2API.getProjectile(this);
        }

        internal function frame18():*
        {
            this.self.stancePlayFrame("start");
        }


    }
}

