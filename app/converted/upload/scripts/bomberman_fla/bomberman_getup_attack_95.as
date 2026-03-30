package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_getup_attack_95 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_getup_attack_95()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10, 17, this.frame18, 19, this.frame20, 22, this.frame23, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame10():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
        }

        internal function frame18():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
        }

        internal function frame20():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame23():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

