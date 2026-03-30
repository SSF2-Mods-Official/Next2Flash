package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_airU_63 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var xSpeedPercent:*;
        public var degreesToAdjustBy:*;
        public var newDirection:*;

        public function fox_airU_63()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 6, this.frame7, 13, this.frame14, 16, this.frame17, 17, this.frame18, 22, this.frame23);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_spark", {"y":-60});
            this.xSpeedPercent = (this.self.getXSpeed() / this.self.getCharacterStat("max_jumpSpeed"));
            this.degreesToAdjustBy = 15;
            if (!this.self.isFacingRight())
            {
                this.degreesToAdjustBy *= -1;
            };
            this.newDirection = (90 - (this.degreesToAdjustBy * this.xSpeedPercent));
            this.self.updateAttackBoxStats(1, {"direction":this.newDirection});
        }

        internal function frame4():*
        {
            this.self.setLandingLag(true);
            this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "damage":11,
                "direction":88,
                "kbConstant":120,
                "power":30,
                "effectSound":"brawl_kick_l"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":10,
                "direction":88,
                "kbConstant":120,
                "power":30,
                "effectSound":"brawl_kick_l"
            });
        }

        internal function frame7():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame14():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }

        internal function frame18():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("fox_landHeavy");
            };
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}

