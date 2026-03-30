package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_dodgeroll_78 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var effect:*;

        public function bomberman_dodgeroll_78()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 8, this.frame9, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame2():*
        {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.effect.scaleX = -(this.effect.scaleX);
        }

        internal function frame3():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame9():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(false);
            };
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

