package gameandwatch_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class NAir_54 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function NAir_54()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6, 8, this.frame9, 10, this.frame11, 11, this.frame12, 14, this.frame15, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
                this.self.setupAutolinkAngle(new Point(0, -25), null);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("beep_nair");
            this.self.setLandingLag(true);
        }

        internal function frame4():*
        {
            this.self.playSound("gw_nairend");
        }

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(1, {"damage":4});
            this.self.updateAttackBoxStats(2, {"damage":4});
            this.self.updateAttackBoxStats(3, {"damage":4});
            this.self.refreshAttackID();
        }

        internal function frame9():*
        {
            this.self.refreshAttackID();
        }

        internal function frame11():*
        {
            this.self.stopAutolinkAngle();
        }

        internal function frame12():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":4,
                "effectSound":"brawl_kick_m",
                "power":40,
                "direction":70,
                "kbConstant":150,
                "weightKB":0,
                "hitStun":2,
                "hitLag":-1.1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":4,
                "effectSound":"brawl_kick_m",
                "power":40,
                "direction":70,
                "kbConstant":150,
                "weightKB":0,
                "hitStun":2,
                "hitLag":-1.1
            });
            this.self.updateAttackBoxStats(3, {
                "damage":4,
                "effectSound":"brawl_kick_m",
                "power":40,
                "direction":70,
                "kbConstant":150,
                "weightKB":0,
                "hitStun":2,
                "hitLag":-1.1
            });
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "damage":3,
                "power":40,
                "direction":70,
                "kbConstant":55,
                "weightKB":0,
                "hitStun":3,
                "hitLag":-1.1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":3,
                "power":40,
                "direction":70,
                "kbConstant":55,
                "weightKB":0,
                "hitStun":3,
                "hitLag":-1.1
            });
            this.self.updateAttackBoxStats(3, {
                "damage":3,
                "power":40,
                "direction":70,
                "kbConstant":55,
                "weightKB":0,
                "hitStun":3,
                "hitLag":-1.1
            });
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("snd_se_GW_Landing02");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

