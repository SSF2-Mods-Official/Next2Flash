package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class UThrowLazer_2 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;

        public function UThrowLazer_2()
        {
            super();
            addFrameScript(0, this.frame1, 15, this.frame16, 17, this.frame18, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.self.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
            };
        }

        internal function frame16():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame18():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame19():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.self.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}

