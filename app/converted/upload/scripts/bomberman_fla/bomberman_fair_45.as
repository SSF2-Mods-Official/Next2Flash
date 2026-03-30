package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_fair_45 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_fair_45()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 13, this.frame14, 15, this.frame16, 16, this.frame17, 21, this.frame22);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(-20),
                "y":-45
            });
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
            if ((this.self.isFacingRight() && (this.self.getXSpeed() < 4.5)) || (!(this.self.isFacingRight()) && (this.self.getXSpeed() > -4.5)))
            {
                this.self.setXSpeed(4.5, false);
            };
        }

        internal function frame14():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }


    }
}

