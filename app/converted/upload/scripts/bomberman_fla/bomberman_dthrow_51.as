package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_dthrow_51 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_dthrow_51()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 13, this.frame14, 14, this.frame15, 15, this.frame16, 19, this.frame20, 24, this.frame25, 29, this.frame30);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame2():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame14():*
        {
            SSF2API.getCamera().shake(4);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame15():*
        {
            this.self.forceGrabbedHurtFrame("faint");
        }

        internal function frame16():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame20():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "damage":7,
                "hasEffect":true,
                "bypassNonGrabbed":true,
                "sdiDistance":1,
                "hitStun":2,
                "selfHitStun":2,
                "effectSound":"brawl_kick_l"
            });
        }

        internal function frame25():*
        {
            SSF2API.getCamera().shake(10);
            this.self.forceGrabbedHurtFrame("downed");
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }


    }
}

