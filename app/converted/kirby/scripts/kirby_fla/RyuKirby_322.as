package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class RyuKirby_322 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var speed:*;
        public var proj:*;

        public function RyuKirby_322()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 6, this.frame7, 29, this.frame30, 30, this.frame31, 31, this.frame32, 35, this.frame36, 36, this.frame37, 59, this.frame60, 60, this.frame61, 61, this.frame62, 65, this.frame66, 66, this.frame67, 89, this.frame90);
        }

        public function countupSpeed(_arg_1:*=null):*
        {
            if (this.self.getControls().BUTTON1)
            {
                this.speed++;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.speed = 0;
            if (SSF2API.isReady() && parent)
            {
                this.self.setGlobalVariable("canCommandCancel", false);
                if (this.self.getGlobalVariable("canShakunetsu"))
                {
                    this.self.resetCommands();
                    gotoAndStop("shakunetsu");
                };
                if (this.self.getGlobalVariable("canHadoken"))
                {
                    this.self.resetCommands();
                    gotoAndStop("command_hadoken");
                };
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, -1, this.countupSpeed);
        }

        internal function frame6():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("effect_ryu_hado1", {
                "x":this.self.flipX(20),
                "y":-15,
                "scaleX":0.5,
                "scaleY":0.5
            });
        }

        internal function frame7():*
        {
            this.self.destroyTimer(this.countupSpeed);
            this.proj = this.self.fireProjectile("hadoken", -30, 6);
            if (this.proj != null)
            {
                this.proj.setXSpeed((this.proj.getXSpeed() + this.self.flipX((this.speed * 0.7))));
                this.proj.updateProjectileStats({"time_max":(this.proj.getProjectileStat("time_max") - (this.speed * 3))});
            };
            this.self.attachEffect("global_dust_heavy");
            this.self.playAttackSound(2);
            this.self.playVoiceSound(2);
            if (!this.self.isOnGround())
            {
                this.self.setYSpeed(-3);
            };
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }

        internal function frame31():*
        {
            this.self.attachEffect("global_spark");
            this.self.attachEffect("global_spark", {"y":-5});
            this.self.attachEffect("global_spark", {"y":-10});
            this.self.attachEffect("global_spark", {"y":-15});
            this.self.playAttackSound(4);
        }

        internal function frame32():*
        {
            this.self.createTimer(1, -1, this.countupSpeed);
        }

        internal function frame36():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("effect_ryu_hado2", {
                "x":this.self.flipX(20),
                "y":-15,
                "scaleX":0.5,
                "scaleY":0.5
            });
        }

        internal function frame37():*
        {
            this.self.destroyTimer(this.countupSpeed);
            this.proj = this.self.fireProjectile("command_hadoken", -30, 6);
            if (this.proj != null)
            {
                this.proj.setXSpeed((this.proj.getXSpeed() + this.self.flipX((this.speed * 0.7))));
                this.proj.updateProjectileStats({"time_max":(this.proj.getProjectileStat("time_max") - (this.speed * 3))});
            };
            this.self.attachEffect("global_dust_heavy");
            this.self.playAttackSound(3);
            this.self.playVoiceSound(3);
            if (!this.self.isOnGround())
            {
                this.self.setYSpeed(-3);
            };
        }

        internal function frame60():*
        {
            this.self.endAttack();
        }

        internal function frame61():*
        {
            this.self.attachEffect("global_spark");
            this.self.attachEffect("global_spark", {"y":-5});
            this.self.attachEffect("global_spark", {"y":-10});
            this.self.attachEffect("global_spark", {"y":-15});
            this.self.playAttackSound(4);
            this.self.createTimer(1, -1, this.countupSpeed);
        }

        internal function frame62():*
        {
            this.self.createTimer(1, -1, this.countupSpeed);
        }

        internal function frame66():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("effect_ryu_hado3", {
                "x":this.self.flipX(20),
                "y":-15,
                "scaleX":0.5,
                "scaleY":0.5
            });
        }

        internal function frame67():*
        {
            this.self.destroyTimer(this.countupSpeed);
            this.proj = this.self.fireProjectile("shakunetsu_hadoken", -30, 6);
            if (this.proj != null)
            {
                this.proj.setXSpeed((this.proj.getXSpeed() + this.self.flipX((this.speed * 0.7))));
                this.proj.updateProjectileStats({"time_max":(this.proj.getProjectileStat("time_max") - (this.speed * 3))});
            };
            this.self.attachEffect("global_dust_heavy");
            this.self.playAttackSound(3);
            this.self.playVoiceSound(4);
            if (!this.self.isOnGround())
            {
                this.self.setYSpeed(-3);
            };
        }

        internal function frame90():*
        {
            this.self.endAttack();
        }


    }
}

