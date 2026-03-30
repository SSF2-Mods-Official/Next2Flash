package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_ledge_attack_85 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_ledge_attack_85()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 9, this.frame10, 11, this.frame12, 12, this.frame13, 17, this.frame18, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame4():*
        {
            this.self.playSound("bomberman_jump1");
        }

        internal function frame9():*
        {
            this.self.setYSpeed(-6);
        }

        internal function frame10():*
        {
            this.self.setXSpeed(8, false);
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

