package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class GetupAttack_85 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function GetupAttack_85()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 11, this.frame12, 17, this.frame18, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame11():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame18():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

