package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class DownTilt_63 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function DownTilt_63()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                this.self.fireProjectile("chibi_dtiltProj");
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}

