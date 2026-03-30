package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class RaymanKirby_320 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var rayman_ground:Boolean;

        public function RaymanKirby_320()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 13, this.frame14, 24, this.frame25, 25, this.frame26, 37, this.frame38, 46, this.frame47, 55, this.frame56, 56, this.frame57, 62, this.frame63, 70, this.frame71, 77, this.frame78, 78, this.frame79, 94, this.frame95, 98, this.frame99, 105, this.frame106, 106, this.frame107, 114, this.frame115);
        }

        public function checkGrabbed():*
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.destroyTimer(this.checkGrabbed);
                if (this.rayman_ground)
                {
                    this.self.stancePlayFrame("grabbed");
                }
                else
                {
                    this.self.stancePlayFrame("grabbed_air");
                };
            };
        }

        public function toFrame(_arg_1:*):*
        {
            this.self.stancePlayFrame("continue");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.createTimer(1, 0, this.checkGrabbed);
                this.rayman_ground = this.self.isOnGround();
                if (!this.rayman_ground)
                {
                    gotoAndStop("rayman_air");
                };
            };
        }

        internal function frame7():*
        {
            SSF2API.playSound("ssf2_snd_sfx_rayman_nspec");
        }

        internal function frame14():*
        {
            this.self.playSound("metal_land_s");
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }

        internal function frame26():*
        {
            this.self.updateAttackStats({
                "air_ease":0,
                "allowControl":false
            });
            this.self.playAttackSound(2);
        }

        internal function frame38():*
        {
            SSF2API.playSound("whoosh1");
        }

        internal function frame47():*
        {
            this.self.updateAttackBoxStats(1, {
                "hasEffect":true,
                "shock":false,
                "effect_id":null,
                "effectSound":"melee_throw",
                "hitStun":0,
                "selfHitStun":0,
                "damage":4
            });
            this.self.refreshAttackID();
            this.self.updateAttackStats({"refreshRate":999999});
        }

        internal function frame56():*
        {
            this.self.endAttack();
        }

        internal function frame57():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame63():*
        {
            SSF2API.playSound("ssf2_snd_sfx_rayman_nspec");
            this.self.setLandingLag(true);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
        }

        internal function frame71():*
        {
            this.self.setLandingLag(false);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
        }

        internal function frame78():*
        {
            this.self.endAttack();
        }

        internal function frame79():*
        {
            this.self.updateAttackStats({
                "air_ease":0,
                "allowControl":false
            });
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.playAttackSound(2);
        }

        internal function frame95():*
        {
            SSF2API.playSound("whoosh1");
        }

        internal function frame99():*
        {
            this.self.updateAttackBoxStats(1, {
                "hasEffect":true,
                "shock":false,
                "effect_id":null,
                "effectSound":"melee_throw",
                "hitStun":0,
                "selfHitStun":0,
                "damage":4
            });
            this.self.refreshAttackID();
            this.self.updateAttackStats({
                "refreshRate":-1,
                "air_ease":-1,
                "allowControl":true
            });
        }

        internal function frame106():*
        {
            this.self.endAttack();
        }

        internal function frame107():*
        {
            SSF2API.getCamera().shake(2);
            this.self.playSound("metal_land_s");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame115():*
        {
            this.self.endAttack();
        }


    }
}

